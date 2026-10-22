pipeline {
    agent { label 'windows-python312' }
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timeout(time: 15, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }
    stages {
        stage('Fresh checkout') {
            steps {
                deleteDir()
                checkout scm
            }
        }
        stage('Windows setup and approved dependencies') {
            steps { bat 'py -3.12 run.py setup' }
        }
        stage('Build analysis and HTTP tests') {
            steps { bat 'py -3.12 run.py check' }
        }
    }
    post {
        always {
            junit testResults: 'reports/tests.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'reports/**,dependencies.sha256.json,requirements.lock,bootstrap.lock', allowEmptyArchive: true
        }
    }
}
