# Your Own Bartender Bot

## Environment

Check prefix in `env.yml` and:

    conda env create -f env.yml

## Configs

## Deployment

    docker build -t bartender .
    docker tag bartender registry.heroku.com/your-own-bartender/web
    docker push registry.heroku.com/your-own-bartender/web
    heroku container:release web