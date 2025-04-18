import json
import torch
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    def __init__(self, data_path):
        with open(data_path, 'r') as f:
            data = json.load(f)
        self.samples = data

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        return sample["message"], sample.get("evidence", None), sample["label"]

def load_data(data_path, batch_size):
    dataset = CustomDataset(data_path)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)