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

-   Node>= `18.x`
-   npm >= `8.18.0`
-   Docker Engine

## Quickstsart

-   Configure your `.env` environment variables from `.env.template`
-   Clone the project: `git clone https://github.com/ZeruiW/xai_service_demo`
-   Change directory into cloned folder: `cd xai_service_demo`
-   docker-compose up --build
-   Install node depencies: `npm i`
-   Start development server: `npm run dev`

# XAI Service Backend

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

## Quickstaart

## TODOs

### Frontend

-   [x] MVP
    -   [ ] Input
        -   [ ] Images
        -   [ ] Map
        -   [ ] Method selector
    -   [x] Data upload
    -   [x] Step-by-step processes
        -   [x] Execute CAM
        -   [x] Run Evaluation
        -   [x] Show Results
    -   [x] Implement Grad CAM
    -   [ ] Implement Grad CAM++
    -   [ ] Implement Layer CAM
-   [ ] Implement custom XAI method
-   [ ] Implement dynamic task group

### Backend

-   [ ] Improve database I/O

### Infrastructure

-   [x] Deploy Frontend
-   [ ] Deploy Backend
