import torch
import transformers
import psutil
import subprocess
import time
import sys
import collections
from transformers import AutoModel, AutoTokenizer
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter

from chatbot.chat_main import DislyteChatBot

def test():
    bot = DislyteChatBot()
    #test_rsp, _ = bot.chat("杨戬云川就业怎么样")
    test_rsp, _ = bot.chat("龙本怎么搭配阵容?")
    bot.summary()
    print("final rsp:")
    print(test_rsp)
    #prompt, references = bot.build_prompt("龙本怎么搭配阵容?")
    #print(prompt)

if __name__ == "__main__":
    test()

