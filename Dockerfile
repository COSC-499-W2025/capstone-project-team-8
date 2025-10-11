# Use official Node.js image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY src/frontend/package.json src/frontend/package-lock.json* ./
RUN npm install

# Copy frontend source code
COPY src/frontend .

# Build the Next.js app
RUN npm run build

# Expose port 3000
EXPOSE 3000

# Start the Next.js app
CMD ["npm", "start"]