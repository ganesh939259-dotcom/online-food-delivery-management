pipeline {

    agent any

    stages {

        stage('Clone') {
            steps {
                git 'https://github.com/ganesh939259-dotcom/online-food-delivery-management.git'
            }
        }

        stage('Install') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                bat 'pytest'
            }
        }

        stage('SonarQube') {
            steps {
                bat 'sonar-scanner'
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker build -t food-order .'
            }
        }

        stage('Run Docker') {
            steps {
                bat 'docker run -d -p 5000:5000 food-order'
            }
        }

    }

}