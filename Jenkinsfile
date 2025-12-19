pipeline {
    agent {
        kubernetes {
            label 'course-recommender-agent'
            defaultContainer 'jnlp'
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    some-label: course-recommender
spec:
  containers:
  - name: dind
    image: docker:dind
    securityContext:
      privileged: true
    volumeMounts:
    - name: docker-config
      mountPath: /etc/docker/daemon.json
      subPath: daemon.json
    - name: workspace-volume
      mountPath: /home/jenkins/agent
  - name: kubectl
    image: bitnami/kubectl:1.30.0   # ✅ Fixed specific version
    command:
      - cat
    tty: true
    env:
      - name: KUBECONFIG
        value: /kube/config
    volumeMounts:
      - name: kubeconfig-secret
        mountPath: /kube/config
        subPath: kubeconfig
      - name: workspace-volume
        mountPath: /home/jenkins/agent
  - name: sonar-scanner
    image: sonarsource/sonar-scanner-cli
    command:
      - cat
    tty: true
    volumeMounts:
      - name: workspace-volume
        mountPath: /home/jenkins/agent
  - name: jnlp
    image: jenkins/inbound-agent:3345.v03dee9b_f88fc-1
    env:
      - name: JENKINS_SECRET
        value: "\${JENKINS_SECRET}"
      - name: JENKINS_TUNNEL
        value: "my-jenkins-agent.jenkins.svc.cluster.local:50000"
    volumeMounts:
      - name: workspace-volume
        mountPath: /home/jenkins/agent
  volumes:
    - name: docker-config
      configMap:
        name: docker-daemon-config
    - name: workspace-volume
      emptyDir: {}
    - name: kubeconfig-secret
      secret:
        secretName: kubeconfig-secret
"""
        }
    }

    environment {
        IMAGE_NAME = 'course-recommender:latest'
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                container('dind') {
                    sh '''
                    set -e
                    docker build -t $IMAGE_NAME .
                    '''
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                container('dind') {
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker tag $IMAGE_NAME $DOCKER_USER/$IMAGE_NAME
                        docker push $DOCKER_USER/$IMAGE_NAME
                        '''
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                container('kubectl') {
                    sh '''
                    kubectl apply -f service.yaml
                    kubectl apply -f deployment.yaml
                    '''
                }
            }
        }
    }

    post {
        failure {
            echo "Build failed. Please check logs."
        }
        success {
            echo "Pipeline completed successfully!"
        }
    }
}
