import os
import openai
import time


api_dict = [
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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",
    "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"
]
regenerate = [
    "a45_b42.txt",
    "a25_b21.txt",
    "a31_b32.txt"
]
#"a22_b22.txt"
#"a23_b21.txt"
cnt = 0
i = 0
num = 0

def solve(file_name, file_path):

    # if (file_name not in regenerate):
    #     return
    global cnt, i, num
    with open(file_path, "r") as file:
        real_content = file.read()
        
    flag = 0
    num_i = 0
    while (flag == 0):
        if (num_i > 15):
            break
        cnt = cnt + 1
        i = i + 1
        print(i, file_name)

        if (cnt > 10):
            num = num + 1
            if (num > 9): 
                num = 0
            cnt = 1
        
        openai.api_key = api_dict[num]
        messages=[{"role": "user", "content": real_content}]
        response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                max_tokens=1024,
                temperature=1.2,
                messages = messages
        )
        real_ans = response['choices'][0]['message']['content']
        
        # check lines
        lines = real_ans.splitlines()
        if len(lines) >= 18:
            flag = 0
            print(real_ans)
            print("步骤超过20行。")
        elif (('or\n' in real_ans) or ('Or\n' in real_ans) or ('OR\n' in real_ans)):
            flag = 0
            print(real_ans)
            print("步骤出现or。")
        else:
            if ("General" not in real_ans):
                print("不general。")
            flag = 1
            print(real_ans)
            save_name = "result/" + file_name
            save_file = open(save_name, 'w', encoding='utf-8')
            save_file.write(real_ans)  
            save_file.close()
        num_i = num_i + 1
        time.sleep(30)


def main():
    directory_path = "paser/"
    result_path = "result/"
    file_list = sorted([f for f in os.listdir(directory_path) if f.endswith('.txt')])
    result_list = sorted([f for f in os.listdir(result_path) if f.endswith('.txt')])
    #print(len(result_list), result_list)

    for file_name in file_list:
        file_path = os.path.join(directory_path, file_name)
        # if (file_name not in regenerate):
        #     continue
        print(file_name)
        solve(file_name, file_path)

if __name__ == "__main__":
    main()

   
   


