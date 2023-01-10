import torch
import platform

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

print('--------')
print('Platform:')
print(platform.platform())
print("Pytorch device: ")
print(device)
# Check PyTorch has access to MPS (Metal Performance Shader, Apple's GPU architecture)
print(
    f"Is MPS (Metal Performance Shader) built? {torch.backends.mps.is_built()}")
print(f"Is MPS available? {torch.backends.mps.is_available()}")
print('--------')
