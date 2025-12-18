pipeline {
    agent {
        kubernetes {
            label 'course-recommender-pod'
            defaultContainer 'jnlp'
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: docker
    image: docker:20.10.24
    command:
    - cat
    tty: true
    volumeMounts:
    - mountPath: /var/run/docker.sock
      name: docker-socket
    - mountPath: /home/jenkins/agent
      name: workspace-volume
  - name: kubectl
    image: bitnami/kubectl:latest
    command:
    - cat
    tty: true
    volumeMounts:
    - mountPath: /home/jenkins/agent
      name: workspace-volume
  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli
    command:
    - cat
    tty: true
    volumeMounts:
    - mountPath: /home/jenkins/agent
      name: workspace-volume
  volumes:
  - name: workspace-volume
    emptyDir: {}
  - name: docker-socket
    hostPath:
      path: /var/run/docker.sock
"""
        }
    }

    environment {
        DOCKER_IMAGE = "course-recommender"
        DOCKER_TAG = "latest"
        NEXUS_URL = "nexus.example.com"  // <-- replace with your Nexus URL
        NEXUS_REPO = "docker-repo"       // <-- replace with your Nexus repository
        SONAR_TOKEN = credentials('sonar-token')  // Jenkins credential ID
        NEXUS_CRED = credentials('nexus-cred')    // Jenkins credential ID
        KUBE_CONFIG = credentials('kubeconfig')   // Jenkins credential ID (optional)
    }

    stages {
        stage('Checkout Code') {
            steps {
                deleteDir()
                git url: 'https://github.com/shalakabajaj/Course-Recommendation.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                container('docker') {
                    sh """
                    docker build --no-cache -t $DOCKER_IMAGE:$DOCKER_TAG .
                    """
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                container('sonar-scanner') {
                    sh """
                    sonar-scanner \
                      -Dsonar.projectKey=2401007_Course_Recommendation_System \
                      -Dsonar.sources=. \
                      -Dsonar.host.url=http://my-sonarqube-sonarqube.sonarqube.svc.cluster.local:9000 \
                      -Dsonar.login=$SONAR_TOKEN
                    """
                }
            }
        }

        stage('Login to Nexus & Push Docker Image') {
            steps {
                container('docker') {
                    sh """
                    echo $NEXUS_CRED_PSW | docker login $NEXUS_URL -u $NEXUS_CRED_USR --password-stdin
                    docker tag $DOCKER_IMAGE:$DOCKER_TAG $NEXUS_URL/$NEXUS_REPO/$DOCKER_IMAGE:$DOCKER_TAG
                    docker push $NEXUS_URL/$NEXUS_REPO/$DOCKER_IMAGE:$DOCKER_TAG
                    """
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    sh """
                    kubectl apply -f k8s/service.yaml
                    """
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace...'
            cleanWs()
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
