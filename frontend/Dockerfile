# Stage 1: Build frontend
FROM node:20-slim AS builder

WORKDIR /app

# Copy package files first to cache node_modules
COPY package*.json ./
RUN npm ci --legacy-peer-deps

# Copy the rest of the source code
COPY . .

# Build the app for production
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy production build files from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Copy runtime config template
COPY public/config/runtime.template.json /usr/share/nginx/html/config/runtime.template.json

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Add entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose port 80 (standard HTTP)
EXPOSE 3000

# Start nginx
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
