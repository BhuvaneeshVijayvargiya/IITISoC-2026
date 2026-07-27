import torch
import torch.nn.functional as F
import os
import random
from model import AI
from feature import extracter
from solver import generate_pct,score_node,place 
from input import load


def generate_labeled_step(scenario_files):
    file=random.choice(scenario_files)
    packages,uld,K=load(file)
    packages2=list(packages)
    random.shuffle(packages2)
    q=random.randint(0,len(packages2)-1)
    for pkg in packages2[:q]:
        pre_nodes=generate_pct(pkg, uld)
        if pre_nodes:
            for node in pre_nodes:
                node.score = score_node(node)
            best = max(pre_nodes, key=lambda n: n.score)
            place(pkg, best)

    package=packages2[q] 

    nodes=generate_pct(package,uld)
    if len(nodes) == 0:
        return None

    for node in nodes:
        node.score=score_node(node)        

    label=0
    best_score=nodes[0].score
    for node in nodes:
        if node.score > best_score:
            best_score = node.score

    tied_best = []
    for i in range(len(nodes)):
        if nodes[i].score==best_score:
            tied_best.append(i)
    label=random.choice(tied_best)

    features=[]
    for node in nodes:
        supported_area = getattr(node, "supported_area", None)
        features.append(extracter(node, supported_area))
    candidates = torch.tensor(features,dtype=torch.float32)

    return candidates, label


def train(model,scenario_files,epochs,steps_per_epoch,lr=1e-4):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    for epoch in range(epochs):
        total_loss,correct,seen=0.0,0,0

        step=0
        while step < steps_per_epoch:
            result = generate_labeled_step(scenario_files)
            if result is None:
                continue   

            candidates,label=result
            scores = model(candidates).unsqueeze(0)  
            target = torch.tensor([label])

            loss=F.cross_entropy(scores,target)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            correct += int(scores.argmax(dim=1).item() == label)
            seen += 1
            step += 1

        print(f"epoch {epoch+1:03d}  loss={total_loss/seen:.4f}  acc={correct/seen:.3f}")

    return model


if __name__ == "__main__":
    input_dir = r"IITISoC-2026\inputs"
    scenario_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir)]
    result = generate_labeled_step(scenario_files)
    candidates, label = result
    print("num candidates:", candidates.shape[0])
    print(candidates)
    print("label:", label)
    model = AI()
    if os.path.exists("pretrained.pt"):
        model.load_state_dict(torch.load("pretrained.pt"))
    train(model, scenario_files, epochs=10, steps_per_epoch=200)
    torch.save(model.state_dict(), "pretrained.pt")