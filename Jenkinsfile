properties([
  pipelineTriggers([]),
  durabilityHint('PERFORMANCE_OPTIMIZED')
])

pipeline {

  agent {
    kubernetes {
      yaml """
apiVersion: v1
kind: Pod
spec:
  containers:

  - name: dind
    image: docker:24-dind
    securityContext:
      privileged: true
    command: ["dockerd-entrypoint.sh"]
    args:
      - "--host=tcp://0.0.0.0:2375"
      - "--insecure-registry=nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
    env:
      - name: DOCKER_TLS_CERTDIR
        value: ""
    volumeMounts:
      - name: docker-storage
        mountPath: /var/lib/docker
      - name: workspace-volume
        mountPath: /home/jenkins/agent

  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli:latest
    command: ["cat"]
    tty: true
    volumeMounts:
      - name: workspace-volume
        mountPath: /home/jenkins/agent

  - name: kubectl
    image: bitnami/kubectl:latest
    command: ["cat"]
    tty: true
    securityContext:
      runAsUser: 0
    volumeMounts:
      - name: workspace-volume
        mountPath: /home/jenkins/agent

  volumes:
    - name: docker-storage
      emptyDir: {}
    - name: workspace-volume
      emptyDir: {}
"""
    }
  }

  options { skipDefaultCheckout() }

  environment {
    APP_NAME      = "course-recommender"
    REGISTRY_HOST = "nexus-service-for-docker-hosted-registry.nexus.svc.cluster.local:8085"
    REGISTRY_REPO = "2401007"
    NAMESPACE     = "2401007"
    IMAGE_TAG     = "${BUILD_NUMBER}"
    DOCKER_HOST   = "tcp://localhost:2375"

    // SonarQube
    SONAR_HOST_URL = "http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000"
    SONAR_PROJECT_KEY = "2401007_course_recommender"
  }

  stages {

    stage('Checkout Code') {
      steps {
        git url: 'https://github.com/shalakabajaj/Course-Recommendation.git', branch: 'main'
      }
    }

    stage('SonarQube Analysis') {
      steps {
        container('sonar-scanner') {
          withCredentials([string(credentialsId: '2401007_Course_Recommendation_System', variable: 'SONAR_TOKEN')]) {
            sh """
              sonar-scanner \
                -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                -Dsonar.sources=. \
                -Dsonar.host.url=${SONAR_HOST_URL} \
                -Dsonar.token=${SONAR_TOKEN}
            """
          }
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        container('dind') {
          sh """
            echo "🔨 Building Docker image..."
            docker build -t ${APP_NAME}:${IMAGE_TAG} .
          """
        }
      }
    }

    stage('Login to Nexus') {
      steps {
        container('dind') {
          withCredentials([usernamePassword(
            credentialsId: 'nexus-docker-creds',
            usernameVariable: 'NEXUS_USER',
            passwordVariable: 'NEXUS_PASS'
          )]) {
            sh """
              echo "${NEXUS_PASS}" | docker login ${REGISTRY_HOST} \
                -u "${NEXUS_USER}" --password-stdin
            """
          }
        }
      }
    }

    stage('Push Image to Nexus') {
      steps {
        container('dind') {
          sh """
            echo "📦 Tagging image..."
            docker tag ${APP_NAME}:${IMAGE_TAG} ${REGISTRY_HOST}/${REGISTRY_REPO}/${APP_NAME}:${IMAGE_TAG}
            docker tag ${APP_NAME}:${IMAGE_TAG} ${REGISTRY_HOST}/${REGISTRY_REPO}/${APP_NAME}:latest

            echo "🚀 Pushing image to Nexus..."
            docker push ${REGISTRY_HOST}/${REGISTRY_REPO}/${APP_NAME}:${IMAGE_TAG}
            docker push ${REGISTRY_HOST}/${REGISTRY_REPO}/${APP_NAME}:latest
          """
        }
      }
    }

    stage('Deploy to Kubernetes') {
      steps {
        container('kubectl') {
          sh """
            echo "☸️ Deploying to Kubernetes..."
            kubectl apply -f deployment.yaml -n ${NAMESPACE}
            kubectl apply -f service.yaml -n ${NAMESPACE}

            echo "⏳ Waiting for rollout..."
            kubectl rollout status deployment/${APP_NAME} -n ${NAMESPACE}
          """
        }
      }
    }
  }

  post {
    success {
      echo "🎉 Course Recommendation System deployed successfully!"
    }
    failure {
      echo "❌ Pipeline failed. Check Jenkins logs."
    }
    always {
      echo "🔁 CI/CD pipeline finished"
    }
  }
}
