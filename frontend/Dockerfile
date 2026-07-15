# Use an official modern Node runtime environment matching your Angular CLI parameters
FROM node:22-slim

# Set the working directory inside the docker container layout
WORKDIR /app

# Install the Angular command line interface globally inside the image space
RUN npm install -g @angular/cli

# Copy configuration files into the container canvas
COPY package*.json ./

# Install all frontend dependencies node modules
RUN npm install

# Copy the rest of the application frontend elements
COPY . .

# Expose port 4200 for client dashboard views
EXPOSE 4200

# Start up the Angular serving engine mapping it to host routes directly
CMD ["ng", "serve", "--host", "0.0.0.0", "--port", "4200"]
