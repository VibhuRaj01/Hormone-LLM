from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os, json
import emotions

history_file = "hist.json"
config = BitsAndBytesConfig(load_in_8bit=True, llm_int8_enable_fp32_cpu_offload=True)

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B-Instruct")
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.1-8B-Instruct",
    device_map="auto",
    quantization_config=config,
    torch_dtype="auto",
)

with open("sys_prompt.txt") as f:
    sys_prompt = f.read()


def check_status(file_name=history_file):
    if not os.path.exists(file_name):
        messages = [{"role": "system", "content": sys_prompt}]
        with open(file_name, "w") as f:
            json.dump(messages, f)


MAX_HISTORY = 10


def history_manager(msg=None, mode="read", file_name=history_file):
    check_status(file_name)
    if mode == "read":
        with open(file_name) as f:
            return json.load(f)
    elif mode == "write":
        with open(file_name) as f:
            messages = json.load(f)
        messages.append({"role": "user", "content": msg})
        # trim old turns (keep system + last N pairs)
        if len(messages) > MAX_HISTORY * 2 + 1:
            messages = [messages[0]] + messages[-MAX_HISTORY * 2 :]
        with open(file_name, "w") as f:
            json.dump(messages, f)
        return messages


def get_out(query: str, max_new_tokens: int = 512) -> str:
    # 1) Update hormone state based on the user query
    try:
        emotions.hormone_state = emotions.update_hormone_levels(
            query, emotions.hormone_state
        )
        emotions.save_state()
    except Exception as e:
        print("Warning: failed to update hormone state:", e)

    # 2) Append the user message to history and get the full convo
    messages = history_manager(query, mode="write")

    # 3) Compose a temporary system prompt with fresh hormone values
    hormone_text = "\n\n### Current Hormone State\n" + "\n".join(
        f"- {k.capitalize()}: {round(v, 2)}" for k, v in emotions.hormone_state.items()
    )
    print(hormone_text)
    tmp_system = {"role": "system", "content": sys_prompt + hormone_text}
    tmp_messages = [tmp_system] + messages[1:]  # skip the original system message

    # 4) Tokenize + generate
    inputs = tokenizer.apply_chat_template(
        tmp_messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    outputs = model.generate(
        **inputs, max_new_tokens=max_new_tokens, temperature=0.5, top_p=0.8
    )
    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[-1] :], skip_special_tokens=True
    )

    # 5) Save assistant reply back into the permanent history
    messages.append({"role": "assistant", "content": response})
    with open(history_file, "w") as f:
        json.dump(messages, f)

    return response


# try:
#     while True:
#         query = input("Input: ")
#         print(get_out(query))
# except KeyboardInterrupt:
#     print("\nExiting...")
