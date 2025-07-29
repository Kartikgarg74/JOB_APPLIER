# Use the official Node.js 18 image as the base image
FROM node:18-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and yarn.lock (or package-lock.json) to the working directory
COPY package.json yarn.lock* ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy the rest of the application code to the working directory
COPY . .

# Build the Next.js application
RUN yarn build

# Expose the port Next.js runs on
EXPOSE 3000

# Command to run the application
CMD ["yarn", "start"]