pipeline {
    agent any

    stages {

        stage('Clone') {
            steps {
                git 'https://github.com/ganesh939259-dotcom/online-food-delivery-management.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                    sonar-scanner \
                    -Dsonar.projectKey=online-food-delivery-management \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=http://13.127.3.51:9000
                    '''
                }
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t food-order .'
            }
        }

    }
}