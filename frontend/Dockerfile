# frontend/Dockerfile
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy dependencies and install
COPY package.json package-lock.json ./
RUN npm install

# Copy source code
COPY . .


# Expose the development server port
EXPOSE 3000

# Start Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
