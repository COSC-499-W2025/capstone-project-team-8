import express from "express";
import axios from "axios";
import cors from "cors";

const app = express();
app.use(express.json());
app.use(cors());

const OLLAMA_API = "http://localhost:11434/api/generate";

app.post("/api/query", async (req, res) => {
  const { prompt, model = "mistral" } = req.body;

  try {
    const response = await axios.post(OLLAMA_API, {
      model,
      prompt,
      stream: false,
    });

    res.json({ success: true, response: response.data.response });
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ success: false, error: err.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`API running on http://localhost:${PORT}`));
