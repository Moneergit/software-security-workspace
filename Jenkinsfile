pipeline {
    agent { label 'python312-linux' }
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
        stage('Verify and install approved artifacts') {
            steps {
                sh '''
                    python3.12 scripts/check_artifacts.py
                    python3.12 -m venv .venv
                    .venv/bin/python -m pip install --no-index --find-links vendor --require-hashes -r bootstrap.lock
                    .venv/bin/python -m pip install --no-index --find-links vendor --require-hashes -r requirements.lock
                '''
            }
        }
        stage('Build static analysis dependencies and HTTP tests') {
            steps { sh '.venv/bin/python scripts/ci.py' }
        }
    }
    post {
        always {
            junit testResults: 'reports/tests.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'reports/**,dependencies.sha256.json,requirements.lock', allowEmptyArchive: true
        }
    }
}
