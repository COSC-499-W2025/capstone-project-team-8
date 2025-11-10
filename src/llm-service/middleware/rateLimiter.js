// Rate limiting store
const rateLimit = {};

// Rate limiting configuration
const RATE_LIMIT = 20;
const TIME_WINDOW = 60 * 1000;

// Custom rate limiting middleware
export const rateLimiter = (req, res, next) => {
  const clientIP = req.ip || req.connection.remoteAddress;
  const now = Date.now();
  
  if (!rateLimit[clientIP]) {
    rateLimit[clientIP] = { count: 1, resetTime: now + TIME_WINDOW };
    return next();
  }
  
  if (now > rateLimit[clientIP].resetTime) {
    rateLimit[clientIP] = { count: 1, resetTime: now + TIME_WINDOW };
    return next();
  }
  
  if (rateLimit[clientIP].count >= RATE_LIMIT) {
    return res.status(429).json({ 
      error: "Too many requests. Try again later.",
      retryAfter: Math.ceil((rateLimit[clientIP].resetTime - now) / 1000)
    });
  }
  
  rateLimit[clientIP].count++;
  next();
};