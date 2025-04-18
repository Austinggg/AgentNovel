import torch
import torch.nn as nn
import torch.optim as optim
from models.llm_extractor import LLMExtractorAPI
from models.dnf_model import DNFModel
from utils.data_loader import load_data
from utils.logic_transform import transform_logic_atoms_to_features
from utils.evaluation import evaluate

def train_dnf_model(train_loader, val_loader, model, criterion, optimizer, device, num_epochs, llm_extractor, predicate_set):
    model.to(device)
    for epoch in range(num_epochs):
        model.train()
        total_loss = 0
        for messages, evidences, labels in train_loader:
            features = []
            for message, evidence in zip(messages, evidences):
                logic_atoms = llm_extractor.extract_logic_atoms(message, evidence)
                features.append(transform_logic_atoms_to_features(logic_atoms, predicate_set))
            features = torch.stack(features).to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(features)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {total_loss:.4f}")

        # 验证模型性能
        val_acc, val_f1 = evaluate_dnf_model(val_loader, model, device, llm_extractor, predicate_set)
        print(f"Validation Accuracy: {val_acc:.4f}, F1 Score: {val_f1:.4f}")

def evaluate_dnf_model(data_loader, model, device, llm_extractor, predicate_set):
    model.eval()
    predictions, true_labels = [], []
    with torch.no_grad():
        for messages, evidences, labels in data_loader:
            features = []
            for message, evidence in zip(messages, evidences):
                logic_atoms = llm_extractor.extract_logic_atoms(message, evidence)
                features.append(transform_logic_atoms_to_features(logic_atoms, predicate_set))
            features = torch.stack(features).to(device)
            labels = labels.to(device)

            outputs = model(features)
            preds = torch.argmax(outputs, dim=1)
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
    acc = accuracy_score(true_labels, predictions)
    f1 = f1_score(true_labels, predictions, average='macro')
    return acc, f1

if __name__ == "__main__":
    # 配置参数
    data_dir = "./data"
    train_path = f"{data_dir}/train.json"
    val_path = f"{data_dir}/val.json"
    test_path = f"{data_dir}/test.json"
    batch_size = 32
    num_features = 10  # 特征数量
    num_conjuncts = 20  # 合取项数量
    num_classes = 2  # 类别数量
    learning_rate = 1e-3
    num_epochs = 10
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 初始化 LLM 提取器
    api_key = "your_openai_api_key"  # 替换为你的 OpenAI API 密钥
    llm_extractor = LLMExtractorAPI(api_key=api_key, model="gpt-3.5-turbo")

    # 定义谓词集合
    predicate_set = ["P1", "P2", "P3", "P4", "P5"]  # 示例谓词集合

    # 加载数据
    train_loader = load_data(train_path, batch_size)
    val_loader = load_data(val_path, batch_size)
    test_loader = load_data(test_path, batch_size)

    # 初始化 DNF 模型
    model = DNFModel(num_features=len(predicate_set), num_conjuncts=num_conjuncts, num_classes=num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # 训练模型
    train_dnf_model(train_loader, val_loader, model, criterion, optimizer, device, num_epochs, llm_extractor, predicate_set)

    # 测试模型
    test_acc, test_f1 = evaluate_dnf_model(test_loader, model, device, llm_extractor, predicate_set)
    print(f"Test Accuracy: {test_acc:.4f}, F1 Score: {test_f1:.4f}")