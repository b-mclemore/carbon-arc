# Build stage
FROM node:18 AS build

WORKDIR /app

COPY package.json .
RUN npm install

COPY tailwind.config.js .
COPY public ./public
COPY src ./src

RUN npm run build

# Production stage
FROM node:18-slim

WORKDIR /app

# Install serve to serve static files
RUN npm install -g serve

# Copy built app from build stage
COPY --from=build /app/build ./build

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
