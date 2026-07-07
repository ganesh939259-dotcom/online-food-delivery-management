pipeline {
    agent any

    stages {

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

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('SonarQube') {
                    sh '''
                    . venv/bin/activate
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
                sh '''
                docker build -t food-order .
                '''
            }
        }

        stage('Run Docker Container') {
            steps {
                sh '''
                docker rm -f food-order-container || true
                docker run -d --name food-order-container -p 5000:5000 food-order
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}