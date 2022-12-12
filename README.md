## docker-compose up --build

Check routes

```bash
flask --app db_service routes
flask --app model_service/resnet50 routes
flask --app xai_service/pytorch_cam routes

```

Run debug mode

```bash
flask --app model_service/resnet50 --debug run -p 5001
flask --app db_service --debug run -p 5002
flask --app xai_service/pytorch_cam --debug run -p 5003
flask --app evaluation_service --debug run -p 5004
```

# XAI Service Frontend

This is the frontend for the eXplainable AI service.

The project uses [Next.js](https://nextjs.org) framework, styled with [Tailwindcss](https://tailwindcss.com), and [Prisma ORM](https://prisma.io).

It is hosted on [Vercel](https://vercel.com).

## Development Prequisites:

-   Node >= `18.x`
-   npm >= `8.18.0`
-   Docker Engine

## Quickstart

-   Configure your `.env` environment variables from `.env.template`
-   Clone the project: `git clone https://github.com/ZeruiW/XAI-Service`
-   Change directory into cloned folder: `cd XAI-Service`
-   Install node depencies: `npm i`
-   Start development server: `npm run dev`

# XAI Service Backend

## Run Docker in Dev Env

### 1. Start-Up Local MySQL

If you are the first time, please also create a volume for MySQL.

``` bash
docker volume create xaifw-mysql
```

Then:

``` bash
docker compose -f backend/db_service/docker-compos-mysql.yaml up -d
```

### 2. Volume for All the Services

``` bash
docker volume create xai_fw_volumes
```

### 3. Bring Up Services

```bash
docker compose -f backend/docker-compose.yml -f backend/docker-compose-dev.yml up --build
```

Or for single service:

```bash
docker compose -f backend/docker-compose.yml -f backend/docker-compose-dev.yml up [service_name] --build
```



## Basic Work Flow

### Case 1. ResNet50 & GradCAM

API Document: https://documenter.getpostman.com/view/2019955/2s8YzUw1he

1. Register four services to central;
2. Upload Dataset;
3. Execute CAM task;
4. Once CAM task finished, execute Evaluation task;





## Requirements

### Platforms

-   [ ] Linux x86-64:
    -   [x] Ubuntu 22.04 LTS (Best)
    -   [x] Debian 11 "Bullseye" Stable branch
    -   [x] RHEL 8
    -   [ ] Arch
-   [ ] Windows x86-64:
    -   [ ] Windows 10 >= 1909 update
    -   [ ] Windows 11

### Hardware Acceleration

-   [ ] NVIDIA CUDA Library
-   [ ] Vulkan

## TODOs

Tasks and child tasks are priority tagged starting from 0 as the highest priority. E.g. `P0`, `P1`,...`Pn`. Finished tasks are stripped of the priority tag.

For maintainers, it is advised to follow the Notion documentation (shared internally) as the single source of truth.

### Frontend

-   [ ] Refactor code base `P0`
    -   This task ensures scalability and extensibility
    -   [ ] Break functions in the Index page into reusable components `P0`
    -   [ ] Rename state functions `P0`
    -   [ ] Clean up unused functions `P1`
    -   [ ] Migrate Web API Fetch() to React/TanStack Query `P2`
-   [x] MVP `P0`
    -   [ ] Input `P0`
        -   [x] Images
        -   [ ] Non-images `P0`
        -   [x] Mapping
        -   [ ] Method selector `P1`
    -   [x] Data upload
    -   [x] Step-by-step processes
        -   [x] Execute CAM
        -   [x] Run Evaluation
        -   [x] Show Results
    -   [x] Implement Grad CAM API
    -   [ ] Implement Grad CAM++ API `P0`
    -   [ ] Implement Layer CAM API `P0`
-   [ ] Implement custom XAI method `P1`
-   [ ] Implement dynamic task group `P1`
-   [ ] Migrate over to DaisyUI instead of the vanilla Tailwindcss `P2`
-   [ ] Write User Stories (on Notion) `P2`

### Backend

> TBA

### Infrastructure

-   [x] Deploy Frontend
-   [ ] Deploy Backend `P0`
