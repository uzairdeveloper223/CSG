# CSG — Colab Script Generator

CSG is a browser-based tool that generates ready-to-run Python scripts for hosting any Ollama-compatible language model on Google Colab. You fill in a form, click generate, and get a self-contained `.py` file that handles everything: installing Ollama, pulling the model, launching a Flask web server with a full chat UI, exposing it through a Cloudflare tunnel, and starting a CLI chat mode — all in one script.

No manual setup, no notebooks to configure. Just run the generated script in a Colab terminal and you have a working AI chat server with a public URL in minutes.

---

## What You Get

Each generated script is a single Python file that, when run on Google Colab, does the following in order:

1. **Installs dependencies** — `requests`, `flask`, `rich`, `psutil`, `GPUtil`, and any other required packages.
2. **Installs Ollama** — Downloads and extracts the Ollama binary.
3. **Starts the Ollama server** — Launches it in the background and waits for it to be ready.
4. **Pulls your chosen model** — Downloads the model weights with a progress bar.
5. **Launches a Flask web server** — Serves a full-featured chat interface on port 7860.
6. **Opens a Cloudflare tunnel** — Creates a public HTTPS URL anyone can use to access the chat.
7. **Starts CLI chat** — Drops into an interactive terminal chat session with rich formatting.

The web UI includes:

- Material You-inspired dark/light theme with accent color switching
- Multi-chat support with history saved in localStorage
- Streaming responses with real-time token display
- Thinking process visualization for reasoning models (collapsible `<think>` blocks)
- System monitor panel showing GPU, VRAM, RAM, and uptime
- Markdown rendering with syntax-highlighted code blocks
- Responsive layout that works on desktop and mobile

---

## Repository Contents

| File | Description |
|------|-------------|
| `index.html` | The generator page. Open it in any browser to configure and generate a Colab script. |
| `huihui_ai_deepseek_r1_abliterated_14b_colab.py` | A pre-generated example script for the `huihui_ai/deepseek-r1-abliterated:14b` model. |
| `README.md` | This file. |

---

## How to Use

### Generating a Script

1. Open `index.html` in your browser (locally or hosted) or [Click Here](http://csg.uzairmughal.dev/).
2. Enter the Ollama model ID (e.g. `huihui_ai/deepseek-r1-abliterated:14b`). You can find model IDs at [ollama.com/library](https://ollama.com/library).
3. Optionally set a display title, your name, a system prompt, and toggle thinking model support.
4. Click **Generate Script**.
5. Download the generated `.py` file or copy the code.

### Running on Google Colab

1. Open [Google Colab](https://colab.research.google.com/).
2. Make sure you have a GPU runtime enabled: **Runtime > Change runtime type > T4 GPU**.
3. Upload your generated `.py` file to `content/`.
4. Open a terminal: **Tools > Terminal** (not a code cell — the `!` prefix breaks rich output).
5. Run:
   ```
   python3 your_script.py
   ```
6. Wait for the setup to complete. The script will print a Cloudflare public URL when ready.
7. Share the URL with anyone, or use the CLI chat directly in the terminal.

### Running the Example Script

The included `huihui_ai_deepseek_r1_abliterated_14b_colab.py` is configured for the DeepSeek-R1 Abliterated 14B model, a reasoning-capable model that fits within the free Colab T4 GPU (15 GB VRAM). Run it the same way as any generated script.

---

## Requirements

- **Google Colab** with a GPU runtime (T4 for free tier, A100 for larger models)
- A modern browser to access the web chat UI
- No local installation needed — everything runs on Colab

### Model Size Guidelines

| Colab Tier | GPU | VRAM | Max Model Size |
|------------|-----|------|----------------|
| Free | T4 | 15 GB | Up to ~14B parameters (quantized) |
| Pro | A100 | 40 GB | Up to ~70B parameters (quantized) |
| Pro+ | A100 | 80 GB | Larger models |

---

## Things to Know

- Always run the script from a **Colab terminal**, not a code cell. The `!` prefix in code cells breaks the rich terminal output and Cloudflare URL detection.
- Free Colab sessions disconnect after roughly 90 minutes of idle time or 12 hours total.
- The Cloudflare tunnel URL changes every time you restart the script.
- Do not close the Colab browser tab while the script is running — the session needs to stay active.
- The generator page works entirely client-side. No data is sent to any server.

---

## Author

Made by [Uzair Mughal](https://github.com/uzairdeveloper223)

---

## License

License: Apache 2.0

## Contributions

Contributions are welcome! Feel free to fork the repository, open an issue, or submit a pull request.

