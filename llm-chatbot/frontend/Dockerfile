FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with exact versions from lock file
RUN npm ci

# Copy application
COPY . .

# Set environment variables with defaults
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://localhost:8000/api}
ENV NEXT_PUBLIC_ORCHESTRATION_URL=${NEXT_PUBLIC_ORCHESTRATION_URL:-http://localhost:8001/api}
ENV NODE_ENV=development

# Expose port
EXPOSE 3000

# Run Next.js directly
CMD ["sh", "-c", "node node_modules/next/dist/bin/next dev"]
