from PIL import Image
import torch
from threading import Lock
from torch import Tensor
import torch.nn.modules.linear
import torch.nn.functional as F

from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from transformers.models.qwen2_vl.modeling_qwen2_vl import Qwen2RMSNorm

from rimo_utils.计时 import 计时
from rimo_storage.cache import disk_cache


model = None
processor = None
_L = Lock()


def _init_model():
    global model, processor

    model = Qwen2VLForConditionalGeneration.from_pretrained(
        "Qwen/Qwen2-VL-7B-Instruct", torch_dtype=torch.bfloat16, device_map="cuda"
    )

    for name, param in model.model.layers.named_parameters():
        if name.endswith('.weight'):
            param.data = param.data.to(torch.float8_e4m3fn)
    def _forward(self, input: Tensor) -> Tensor:
        if self.weight.dtype is not torch.float8_e4m3fn:
            return F.linear(input, self.weight, self.bias)
        n = None
        if len(input.shape) > 2:
            n = input.shape[0]
            input = input.reshape(input.shape[0]*input.shape[1], *input.shape[2:])
        res2, _ = torch._scaled_mm(input.to(torch.float8_e4m3fn), self.weight.T, out_dtype=torch.bfloat16, bias=self.bias)
        res2 = res2.nan_to_num(0)
        if n:
            res2 = res2.reshape(n, res2.shape[0] // n, *res2.shape[1:])
        return res2


    def norm_forward(self, hidden_states):
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(variance + self.variance_epsilon)
        return self.weight.to(torch.bfloat16) * hidden_states.to(input_dtype)


    Qwen2RMSNorm.forward = norm_forward
    torch.nn.modules.linear.Linear.forward = _forward
    torch.cuda.empty_cache()

    processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-7B-Instruct")


@disk_cache(serialize='pickle')
def 问(image: Image, prompt: str, **kwargs) -> str:
    with _L:
        if not model:
            _init_model()
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": prompt},
            ],
        }
    ]
    text_prompt = processor.apply_chat_template(messages, add_generation_prompt=True)
    inputs = processor(
        text=[text_prompt], images=[image], padding=True, return_tensors="pt"
    ).to("cuda")
    generated_ids = model.generate(**inputs, **kwargs)
    generated_ids_trimmed = [
        out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    return output_text[0]


def 超问(image: Image, prompt: str, **kwargs) -> str:
    res = 问(image, prompt, **kwargs).lower()
    # print(f'「{prompt}」->「{res}」')
    return res
