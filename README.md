# IITISoC 2026 — Intelligent Cargo Packing & Spatial Neuro-Optimization

**Domain:** AI / ML

**Problem Statement:** [View PS details](https://drive.google.com/file/d/1e0F_648dKCm4njNmNO459wFf9FscmqZq/view?usp=drive_link)

**Team Members:**
- Tanush Bansal (Team Leader)
- Arush Agarwal
- Bhuvaneesh Vijayvargiya
- Ranveer Singh Thakur

**Live Demo:** [Click Here](https://aiml-17iitisoc26.streamlit.app/)

---

## About the Project

Airlines and cargo companies load goods into large standard-sized containers called **ULDs (Unit Load Devices)**, before these containers are loaded onto the plane. Deciding exactly what goes where inside each ULD is a surprisingly hard problem — we have to fit as many packages as possible into a limited space, without breaking any physical rules, and without wasting room.

This is a well-known problem in computer science called the **3D Bin Packing Problem**.

This project builds a system that automatically decides:

- **Which package** goes into **which ULD**
- **Where exactly** it should be placed (the x, y, z position)
- **Which way** it should be rotated

so that the loading is safe, stable, and space-efficient, while making sure high-priority cargo always get loaded first. A **machine learning model** helps guide these decisions intelligently, instead of relying only on fixed, hardcoded rules.

---

## The Problem, In Simple Words

Imagine packing boxes into a suitcase:

- Some boxes are heavier, some are lighter.
- You can't place heavy box floating in mid-air — it needs support underneath.
- You can't put too much weight in one suitcase.
- Some boxes are "priority" and must go in.
- You want to use the space as efficiently as possible so no space is wasted.
- You can rotate boxes in different directions to fit them better.

Now imagine doing this for hundreds of packages, across multiple ULDs, at once — that's exactly the challenge this project solves using code and AI.

---

## Our Approach

### 1. Building the Search Space

For every package, the program looks at all the empty corner points inside every ULD (called **extreme points**), and for every possible rotation of the package, checks whether it can physically fit there — without colliding with anything already placed, without sticking outside the ULD, and without exceeding the weight limit.

All valid placement options are collected as **candidate**. This list of candidates is referred to in the code as the **PCT (Placement Candidate Tree)**.

### 2. Scoring Each Candidate

Once we have several valid ways to place a package, we need to pick the best one. Each candidate placement is scored based on factors such as:

- How much it improves space utilization inside the ULD
- Whether it keeps the load balanced (center of gravity close to the ULD's center)
- Whether priority cargo is going into a ULD that already has some priority package in it.

### 3. Neuro-Optimization — the AI Part

Instead of relying only on a manually written scoring formula, we train a small **neural network** (a feed-forward network built with **PyTorch**) to learn how to rank candidate placements. The model looks at a set of numeric features for each placement — volume used, distance from the center, weight ratio, wall/floor contact for support, and more — and learns to predict which candidate is the best choice, based on training examples.

This is what we mean by **Spatial Neuro-Optimization**: using a neural network to help search through the huge number of possible spatial arrangements and guide the algorithm toward good packing decisions, rather than blindly trying every possibility.

We also use a **Beam Search** strategy — instead of keeping only the single best option at every step, we track several good branches (3 to be exact) at once, explore them further, and pick the best overall outcome at the end. This helps avoid getting stuck with a decision that looked good short-term but turns out poorly later.

### 4. Constraints We Handle

While placing packages, the system always respects:

- **Weight limits** — A ULD can never be loaded beyond its maximum weight capacity.
- **Volume utilization** — The system tries to use as much of the ULD's space as possible, minimizing wasted gaps.
- **Physical stability** — A package cannot float in mid-air. It needs a minimum supporting surface area underneath it (from other packages or the floor), otherwise it's considered unstable and not allowed.
- **Balance / Center of gravity** — The system checks how far the overall center of gravity is from the ULD's center and tries to keep loads balanced instead of everything piling onto one side.
- **Spatial orientation** — Every package can be rotated in different ways , and the system checks all valid rotations to find the best fit.
- **Priority handling** — Priority packages are always attempted first, and ULDs carrying at least one priority package are tracked separately, since they cost extra.

---

## Project Structure

```
├── inputs/               # Sample input data sets (package & ULD details in .csv format)
├── ULDs.py               # ULD object : size, weight limit, current load
├── packages.py           # Package object: dimensions, weight, type, and rotations
├── input.py              # Reads and loads input CSV data into Package/ULD objects
├── feature.py            # Converts a placement candidate into numeric features for the model
├── solver.py             # Core placement logic: finds, scores, and picks best placements
├── main.py               # It is for UI and running the code
├── model.py              # Neural network (PyTorch) used to rank placement candidates
├── beam_store.py         # Tracks and stores branches explored during beam search
├── pct.py / pct_store.py # Placement Candidate Tree helpers: representation & storage
├── stability.py          # Checks whether a placed package is physically stable
├── output.py             # Formats and writes out the final packing results
├── visualize.py          # 3D visualization of package arrangement inside ULDs
└── train.py              # Trains the neural network on generated example scenarios

```

---

## Tech Stack

- **Python**
- **PyTorch** — neural network model & training
- **Pandas** — reading/processing the input data
- **Plotly** — 3D visualization of packed ULDs
- **Streamlit** — for UI and deployment
