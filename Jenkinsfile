pipeline {

    agent any

    tools {
        sonarRunner 'SonarScanner'
    }

    stages {

        stage('Clone') {
            steps {
                git branch: 'master',
                    url: 'https://github.com/ganesh939259-dotcom/online-food-delivery-management.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                . venv/bin/activate
                pytest
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                    . venv/bin/activate
                    sonar-scanner
                    '''
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t food-order .'
            }
        }

        stage('Run Docker') {
            steps {
                sh '''
                docker rm -f food-order-container || true
                docker run -d --name food-order-container -p 5000:5000 food-order
                '''
            }
        }
    }
}