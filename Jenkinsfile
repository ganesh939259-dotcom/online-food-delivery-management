pipeline {
    agent any

    environment {
        ACCOUNT_SID   = credentials('twilio-account-sid')
        AUTH_TOKEN    = credentials('twilio-auth-token')
        TWILIO_NUMBER = credentials('twilio-number')
    }

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
                    /opt/sonar-scanner/bin/sonar-scanner \
                    -Dsonar.projectKey=online-food-delivery-management \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=http://13.127.3.51:9000
                    '''
                }
            }
        }

        stage('Build Images') {
            steps {
                sh 'docker compose build'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                docker compose down
                docker compose up -d
                '''
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                sleep 10
                curl -f http://localhost:5000 || (docker compose logs web && exit 1)
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline executed successfully! App deployed at http://13.127.3.51:5000'
        }
        failure {
            echo 'Pipeline failed.'
            sh 'docker compose logs --tail=50 || true'
        }
    }
}