export const requireApiKey = (req, res, next) => {
  const LLM_API_KEY = process.env.LLM_API_KEY;
  const apiKey = req.headers['x-api-key'] || 
                 req.headers['X-API-KEY'] ||
                 req.headers['X-Api-Key'] ||
                 req.query.apikey;
  
  if (!apiKey || apiKey !== LLM_API_KEY) {
    return res.status(401).json({ 
      error: "Invalid or missing API key. Include 'x-api-key' header or 'apikey' query parameter.",
      receivedKey: apiKey ? "Key received but doesn't match" : "No key received",
      expectedFormat: "x-api-key header"
    });
  }
  
  next();
};