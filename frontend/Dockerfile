FROM oven/bun:latest

WORKDIR /app

COPY package.json .
RUN bun install
COPY . .

# start app
CMD ["bun", "run", "dev", "--host"]