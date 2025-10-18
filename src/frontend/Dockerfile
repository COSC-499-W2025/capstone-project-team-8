# Use official Node.js image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY ./package.json ./package-lock.json* ./
RUN npm ci

# Copy frontend source code
COPY . .

# Expose port 3000
EXPOSE 3000

# Start the Next.js app
CMD ["npm", "run", "dev"]
