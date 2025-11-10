# Use official Node.js LTS image
FROM node:20-slim

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json first
# This allows Docker to cache npm install unless dependencies change
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY . .

# Expose the port your frontend uses (e.g., 3000)
EXPOSE 3000

# Start the frontend
CMD ["npm", "start"]
