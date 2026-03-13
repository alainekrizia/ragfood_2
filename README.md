Here’s a clear, beginner-friendly `README.md` for your RAG project, designed to explain what it does, how it works, and how someone can run it from scratch.

---

## 📄 `README.md`

````markdown
# 🧠 RAG-Food: Simple Retrieval-Augmented Generation with ChromaDB + Ollama

This is a **minimal working RAG (Retrieval-Augmented Generation)** demo using:

- ✅ Local LLM via [Ollama](https://ollama.com/)
- ✅ Local embeddings via `mxbai-embed-large`
- ✅ [ChromaDB](https://www.trychroma.com/) as the vector database
- ✅ A simple food dataset in JSON (Indian foods, fruits, etc.)

---

## 🎯 What This Does

This app allows you to ask questions like:

- “Which Indian dish uses chickpeas?”
- “What dessert is made from milk and soaked in syrup?”
- “What is masala dosa made of?”

It **does not rely on the LLM’s built-in memory**. Instead, it:

1. **Embeds your custom text data** (about food) using `mxbai-embed-large`
2. Stores those embeddings in **ChromaDB**
3. For any question, it:
   - Embeds your question
   - Finds relevant context via similarity search
   - Passes that context + question to a local LLM (`llama3.2`)
4. Returns a natural-language answer grounded in your data.

---

## 📦 Requirements

### ✅ Software

- Python 3.8+
- Ollama installed and running locally
- ChromaDB installed

### ✅ Ollama Models Needed

Run these in your terminal to install them:

```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
````

> Make sure `ollama` is running in the background. You can test it with:
>
> ```bash
> ollama run llama3.2
> ```

---

## 🛠️ Installation & Setup

### 1. Clone or download this repo

```bash
git clone https://github.com/yourname/rag-food
cd rag-food
```

### 2. Install Python dependencies

```bash
pip install chromadb requests
```

### 3. Run the RAG app

```bash
python rag_run.py
```

If it's the first time, it will:

* Create `foods.json` if missing
* Generate embeddings for all food items
* Load them into ChromaDB
* Run a few example questions

---

## 📁 File Structure

```
rag-food/
├── rag_run.py       # Main app script
├── foods.json       # Food knowledge base (created if missing)
├── README.md        # This file
```

---

## 🧠 How It Works (Step-by-Step)

1. **Data** is loaded from `foods.json`
2. Each entry is embedded using Ollama's `mxbai-embed-large`
3. Embeddings are stored in ChromaDB
4. When you ask a question:

   * The question is embedded
   * The top 1–2 most relevant chunks are retrieved
   * The context + question is passed to `llama3.2`
   * The model answers using that info only

---

## 🔍 Try Custom Questions

You can update `rag_run.py` to include your own questions like:

```python
print(rag_query("What is tandoori chicken?"))
print(rag_query("Which foods are spicy and vegetarian?"))
```

---

## 🚀 Next Ideas

* Swap in larger datasets (Wikipedia articles, recipes, PDFs)
* Add a web UI with Gradio or Flask
* Cache embeddings to avoid reprocessing on every run

---

## 👨‍🍳 Credits

Made by Callum using:

* [Ollama](https://ollama.com)
* [ChromaDB](https://www.trychroma.com)
* [mxbai-embed-large](https://ollama.com/library/mxbai-embed-large)
* Indian food inspiration 🍛

Alaine Demate and project customization overview
- List of 15 new food items added with brief descriptions
   -Lechon is a Filipino roasted whole pig with crispy golden skin, served at celebrations and special occasions

   - Sinigang is a Filipino sour soup made with pork or seafood, tamarind, and vegetables.

   - Patatim is a Filipino braised pork dish cooked in soy sauce, vinegar, and spices.

   - Pancit Bihon is a Filipino stir-fried rice noodle dish with vegetables and meat or seafood.

   - Sisig is a Filipino dish made with chopped meat, liver, and onions cooked on a hot griddle with vinegar and spices.

   - Salmon is a pink-fleshed fish rich in omega-3 fatty acids, highly nutritious and versatile.

   - Blueberries are small, round berries with a deep blue color and a sweet-tart flavor, packed with antioxidants.

   - Spinach is a dark green leafy vegetable rich in iron, vitamins, and minerals, commonly used in salads and cooked dishes.

   - Avocados are creamy fruits with a large pit, rich in healthy fats and often used in salads, guacamole, and toast.

   - Mangoes are tropical stone fruits with sweet, juicy flesh, known as the king of fruits.

   - Pasta Carbonara is an Italian main course made with pasta, guanciale, eggs, and Pecorino cheese.

   - Sweet and Sour Pork is a Chinese stir-fry dish made with pork, bell peppers, and pineapple in a tangy sweet and sour sauce.

   - Burritos are Mexican wraps made with a large flour tortilla filled with rice, beans, meat, and toppings.

   - Tiramisu is an Italian dessert made with layers of sponge fingers dipped in coffee and mascarpone cream, dusted with cocoa.

   - Green Curry is a Thai curry made with green chili peppers, coconut milk, bamboo shoots, and basil.

- Personal Reflection
   - In all honesty, this is all out of my comfort zone. Even as I am learning how the ropes are tied, I am still a bit unclear with how well I am doing. But things are working on my end - so that should count, right? I am learning new things every time, and it has been both an honor and a joy to see things work. RAG is something I never thought I'd touch, yet here I am, and I do have to say, I am seeing the appeal and efficiency of AI in the use of programming and coding for data. Having AI be used in the form of analyzing data and answering inquiries is very effective - and even more so when I am seeing it build something to life. Learning about AI really does change things and perspectives. Personally, as someone studying business management, these AI tools are so efficient and effective in the aspect of research and development, from data analysis to summarizing facts to make an inference. I want to learn more and see it come to fruition, so I will keep trying to succeed and will fail through the processes to get there.
