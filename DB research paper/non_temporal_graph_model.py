import torch
import torch.nn.functional as F
from torch_geometric.nn import HeteroConv, SAGEConv, Linear
from relbench.datasets import get_dataset
from relbench.tasks import get_task
from relbench.modeling.graph import make_pkey_fkey_graph
from torch_frame import stype
import pandas as pd

# Load dataset and task
dataset = get_dataset("rel-trial", download=True)
task = get_task("rel-trial", "study-outcome", download=True)

# Get underlying database object to build graph
db = dataset.get_db()

# CLEANING: Convert problematic numerical and datetime columns properly

# Clean 'studies' table date and numeric columns
studies_df = db.table_dict['studies'].df.copy()
studies_df['start_date'] = pd.to_datetime(studies_df['start_date'], errors='coerce')  # keep as datetime64[ns]
studies_df['enrollment'] = pd.to_numeric(studies_df['enrollment'], errors='coerce')
db.table_dict['studies'].df = studies_df

# Define col_to_stype_dict mapping feature types; no '__const__' keys
col_to_stype_dict = {
    "studies": {
        "nct_id": stype.categorical,
        "phase": stype.categorical,
        "enrollment": stype.numerical,
        "start_date": stype.numerical,  # handled internally as datetime64
    },
    "sites": {
        "facility_id": stype.categorical,
        "city": stype.categorical,
    },
    # Empty dictionaries for tables without features
    "outcomes": {},
    "interventions_studies": {},
    "drop_withdrawals": {},
    "sponsors": {},
    "outcome_analyses": {},
    "designs": {},
    "facilities_studies": {},
    "eligibilities": {},
    "conditions": {},
    "sponsors_studies": {},
    "reported_event_totals": {},
    "facilities": {},
    "conditions_studies": {},
    "interventions": {},
}

# Build heterogeneous graph
hetero_graph, col_stats_dict = make_pkey_fkey_graph(db, col_to_stype_dict)
print("Graph metadata:", hetero_graph.metadata())

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
hetero_graph = hetero_graph.to(device)

# Define hetero GNN model
class HeteroGNN(torch.nn.Module):
    def __init__(self, metadata, hidden_channels=64, out_channels=2):
        super().__init__()
        self.conv1 = HeteroConv({
            etype: SAGEConv((-1, -1), hidden_channels) for etype in metadata[1]
        }, aggr='mean')
        self.conv2 = HeteroConv({
            etype: SAGEConv((-1, -1), hidden_channels) for etype in metadata[5]
        }, aggr='mean')
        self.linear = Linear(hidden_channels, out_channels)

    def forward(self, x_dict, edge_index_dict):
        x_dict = self.conv1(x_dict, edge_index_dict)
        x_dict = {k: x.relu() for k, x in x_dict.items()}
        x_dict = self.conv2(x_dict, edge_index_dict)
        return self.linear(x_dict['studies'])  # target node type

model = HeteroGNN(hetero_graph.metadata()).to(device)

# Load train, val, test splits and labels for 'studies'
train_idx = torch.tensor(task.get_idx_split("train")).to(device)
val_idx = torch.tensor(task.get_idx_split("val")).to(device)
test_idx = torch.tensor(task.get_idx_split("test")).to(device)
labels = torch.tensor(task.get_node_labels("studies")).to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=0.005)
criterion = torch.nn.CrossEntropyLoss()

def train():
    model.train()
    optimizer.zero_grad()
    out = model(hetero_graph.x_dict, hetero_graph.edge_index_dict)
    loss = criterion(out[train_idx], labels[train_idx])
    loss.backward()
    optimizer.step()
    return loss.item()

def evaluate(idx):
    model.eval()
    with torch.no_grad():
        out = model(hetero_graph.x_dict, hetero_graph.edge_index_dict)
        pred = out[idx].argmax(dim=1)
        correct = (pred == labels[idx]).sum()
        return int(correct) / len(idx)

# Training loop
for epoch in range(1, 51):
    loss = train()
    val_acc = evaluate(val_idx)
    print(f"Epoch {epoch} | Loss: {loss:.4f} | Validation Accuracy: {val_acc:.4f}")

# Test accuracy
test_acc = evaluate(test_idx)
print(f"Test Accuracy: {test_acc:.4f}")
