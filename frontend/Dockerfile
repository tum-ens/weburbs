FROM node:lts-alpine AS build-stage

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:stable-alpine AS production-stage

# Copy entrypoint and nginx config
WORKDIR /app
COPY entrypoint.sh .
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Copy built files
COPY --from=build-stage /app/dist /usr/share/nginx/html

CMD ["/app/entrypoint.sh"]