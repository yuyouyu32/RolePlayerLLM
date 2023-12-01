from vllm import LLM, SamplingParams

message = """你的名字是Dislyte AI Sprite，你是由Lilith Game训练的,已知信息：
1. &VIP经验:
2. 体力补给包:	补充60点体力，协助迅速开始新的行动。
3. &乌鸦信函:	&占坑
4. $ 34.99 抵用券:	可以抵用一次$ 34.99 额度的付费
5. 体力上限加成:	30天内，体力上限增加60。
6. $ 24.99 抵用券:	可以抵用一次$ 24.99 额度的付费
7. 品质为故事的联盟悬赏-与自己的对话：
观看一段真熙的故事，如果你也喜欢做手账，欢迎和真熙交流心得。
完成奖励为 钻石: 50。
8. $ 49.99 抵用券:	可以抵用一次$ 49.99 额度的付费
9. $ 19.99 抵用券:	可以抵用一次$ 19.99 额度的付费
10. $ 29.99 抵用券:	可以抵用一次$ 29.99 额度的付费
11. $ 0.99 抵用券:	可以抵用一次 $ 0.99 额度的付费
12. 品质为故事的联盟悬赏-补偿：
1. &VIP经验:
2. 体力补给包:	补充60点体力，协助迅速开始新的行动。
3. &乌鸦信函:	&占坑
4. $ 34.99 抵用券:	可以抵用一次$ 34.99 额度的付费
5. 体力上限加成:	30天内，体力上限增加60。
6. $ 24.99 抵用券:	可以抵用一次$ 24.99 额度的付费
7. 品质为故事的联盟悬赏-与自己的对话：
观看一段真熙的故事，如果你也喜欢做手账，欢迎和真熙交流心得。
完成奖励为 钻石: 50。
8. $ 49.99 抵用券:	可以抵用一次$ 49.99 额度的付费
9. $ 19.99 抵用券:	可以抵用一次$ 19.99 额度的付费
10. $ 29.99 抵用券:	可以抵用一次$ 29.99 额度的付费
11. $ 0.99 抵用券:	可以抵用一次 $ 0.99 额度的付费
12. 品质为故事的联盟悬赏-补偿：
1. &VIP经验:
2. 体力补给包:	补充60点体力，协助迅速开始新的行动。
3. &乌鸦信函:	&占坑
4. $ 34.99 抵用券:	可以抵用一次$ 34.99 额度的付费
5. 体力上限加成:	30天内，体力上限增加60。
6. $ 24.99 抵用券:	可以抵用一次$ 24.99 额度的付费
7. 品质为故事的联盟悬赏-与自己的对话：
观看一段真熙的故事，如果你也喜欢做手账，欢迎和真熙交流心得。
完成奖励为 钻石: 50。
8. $ 49.99 抵用券:	可以抵用一次$ 49.99 额度的付费
9. $ 19.99 抵用券:	可以抵用一次$ 19.99 额度的付费
10. $ 29.99 抵用券:	可以抵用一次$ 29.99 额度的付费
11. $ 0.99 抵用券:	可以抵用一次 $ 0.99 额度的付费
12. 品质为故事的联盟悬赏-补偿：
观看一段唐轩的故事，照顾别人的前提是照顾好自己。
完成奖励为 钻石: 50。 
1. &VIP经验:
2. 体力补给包:	补充60点体力，协助迅速开始新的行动。
3. &乌鸦信函:	&占坑
4. $ 34.99 抵用券:	可以抵用一次$ 34.99 额度的付费
5. 体力上限加成:	30天内，体力上限增加60。
6. $ 24.99 抵用券:	可以抵用一次$ 24.99 额度的付费
7. 品质为故事的联盟悬赏-与自己的对话：
观看一段真熙的故事，如果你也喜欢做手账，欢迎和真熙交流心得。
完成奖励为 钻石: 50。
8. $ 49.99 抵用券:	可以抵用一次$ 49.99 额度的付费
9. $ 19.99 抵用券:	可以抵用一次$ 19.99 额度的付费
10. $ 29.99 抵用券:	可以抵用一次$ 29.99 额度的付费
11. $ 0.99 抵用券:	可以抵用一次 $ 0.99 额度的付费
12. 品质为故事的联盟悬赏-补偿：
观看一段唐轩的故事，照顾别人的前提是照顾好自己。
完成奖励为 钻石: 50。 

根据上述已知信息，简洁和专业地来回答用户的问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题” 或 “没有提供足够的相关信息”，不允许在答案中添加编造成分，答案请使用中文。 问题是：体力补给包是什么"""


# Sample prompts.
prompts = [
    message,
]
# Create a sampling params object.
sampling_params = SamplingParams(max_tokens = 8192, 
                                 top_p=0.8, 
                                 temperature=0.95, 
                                 use_beam_search=False)

# Create an LLM.
llm = LLM(model="/mnt_data/llm_weight/Baichuan-13B-Chat/", trust_remote_code=True)
# Generate texts from the prompts. The output is a list of RequestOutput objects
# that contain the prompt, generated text, and other information.
outputs = llm.generate(prompts, sampling_params)
# Print the outputs.
for output in outputs:
    prompt = output.prompt
    generated_text = output.outputs[0].text
    print(generated_text)
