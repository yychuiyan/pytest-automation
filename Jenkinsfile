pipeline {
  agent { docker { image 'registry/pytest-automation/runner:v1.0.0'; args '--network host' } }
  options { timeout(time: 30, unit: 'MINUTES'); disableConcurrentBuilds() }

  parameters {
    choice(name: 'TEST_SUITE',
           choices: ['smoke', 'regression', 'all'],
           description: 'smoke=冒烟 | regression=冒烟+回归 | all=全量')
  }

  environment { CI = 'true' }

  stages {
    stage('Setup Environment') {
      steps {
        sh 'ln -sf /app/.venv ./.venv'
        withCredentials([file(credentialsId: 'api-auto-env', variable: 'ENV_FILE')]) {
          sh 'cp $ENV_FILE .env'
        }
      }
    }
    stage('Run Tests') {
      steps {
        script {
          def f = ''
          switch (params.TEST_SUITE) {
            case 'smoke': f = '-m smoke'; break
            case 'regression': f = '-m "smoke or regression"'; break
            case 'all': f = ''; break
          }
          sh "uv run pytest ${f}"
        }
      }
    }
  }
  post {
    always {
      junit testResults: 'reports/junit.xml', allowEmptyResults: true
      archiveArtifacts artifacts: 'reports/pytest-html/**', allowEmptyArchive: true
      sh 'rm -rf reports/ .pytest_cache/'
    }
  }
}
