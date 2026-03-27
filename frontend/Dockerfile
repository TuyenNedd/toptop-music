FROM node:22-slim

WORKDIR /app

# Install dependencies (cached layer)
COPY package.json package-lock.json ./
RUN npm ci

# Copy application source
COPY . .

# Dev: Next.js dev server with Turbopack (source mounted as volume)
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]

EXPOSE 3000
