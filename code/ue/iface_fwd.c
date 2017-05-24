#include <stdio.h>
#include <string.h>
#include <pthread.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>
#include <errno.h>

#define LOCAL_PORT      2001
#define FWD_LTE_PORT    2002
#define FWD_D2D_PORT    2003
#define THREADS_NUM     2
#define BUFFER_SIZE     1450

pthread_t               t_id [THREADS_NUM]; //ids for threads
pthread_cond_t          tx_cond [THREADS_NUM];
pthread_mutex_t         mutex [THREADS_NUM];

char                    recv_buff [BUFFER_SIZE]; //shared variable. Read-only.
int                     sockfd[THREADS_NUM+1]; // Close all sockets when prgm is interrupted
int                     bytes = 0; //shared variable. Read-only


typedef struct input_thread
{
    int sockfd;
    struct sockaddr serv_addr;
    int id;
} 
input_t;

void intHandler() {
    unsigned int i = 0;
    void *status;

    for (i = 0; i < THREADS_NUM; i++)
    {
        close(sockfd[i]);
        pthread_mutex_destroy(&mutex[i]);
        pthread_cond_destroy(&tx_cond[i]);
        pthread_join(t_id[i], &status);
    }
    close(sockfd[THREADS_NUM]);
    printf("\nClear! \n");
    exit(0);
}

// Routine for consumer threads
void * send_data(void *input_args)
{
    input_t * args = (input_t*)input_args;

    if( connect(args->sockfd, (struct sockaddr *)&(args->serv_addr), 
        sizeof(args->serv_addr)) < 0)
    {
       printf("Thread %i  | Error : Connect Failed \n", args->id);
       pthread_exit(0);
    }

    struct sockaddr_in* addr = (struct sockaddr_in*) &(args->serv_addr);
    printf("Thread %i  | Connected to %s\n", 
        args->id , inet_ntoa(addr->sin_addr)); 

    while(1)
    {
        pthread_mutex_lock(&mutex [args->id]);
        pthread_cond_wait(&tx_cond [args->id], &mutex [args->id]);
        printf("Thread %i | Sending packet: %i bytes\n", args->id, strlen(recv_buff));
        sendto(args->sockfd, recv_buff, bytes, 0, NULL, 0); 
        pthread_mutex_unlock(&mutex [args->id]);
    }
} 

int main (int argc, char *argv[])
{
    if (argc != 2 )
    {
        printf("%s <D2D IP Address>\n", argv[0]);
        exit(0);
    }

    int connfd = 0;
    struct sockaddr_in addrs[THREADS_NUM+1];
    char* d2d_addr = argv[1];

    sockfd[THREADS_NUM] = socket(AF_INET, SOCK_STREAM, 0);
    memset(&addrs[THREADS_NUM], '0', sizeof(struct sockaddr));
    memset(recv_buff, '0', sizeof(recv_buff)); 

    addrs[THREADS_NUM].sin_family = AF_INET;
    addrs[THREADS_NUM].sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addrs[THREADS_NUM].sin_port = htons(LOCAL_PORT); 

    bind(sockfd[THREADS_NUM], (struct sockaddr*)&addrs[THREADS_NUM], sizeof(struct sockaddr_in));
    
    // Catching ctrl-C signal
    signal(SIGINT, intHandler);
    signal(SIGPIPE, intHandler);

    // Loopback address
    memset(&addrs[0], '0', sizeof(struct sockaddr));
    addrs[0].sin_family = AF_INET;
    addrs[0].sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addrs[0].sin_port = htons(FWD_LTE_PORT);

    // D2D address
    memset(&addrs[1], '0', sizeof(struct sockaddr));
    addrs[1].sin_family = AF_INET;
    addrs[1].sin_addr.s_addr = inet_addr(d2d_addr);
    addrs[1].sin_port = htons(FWD_D2D_PORT);

    input_t thread_input[THREADS_NUM]; //input for threads

    unsigned int i = 0;
    int rc = 0;
    //Creates the mutexes and threads
    for (i = 0; i < THREADS_NUM; i++) 
    {
        pthread_mutex_init (&mutex[i], NULL);
        pthread_cond_init(&tx_cond[i], NULL);

        memcpy((struct sockaddr*)&(thread_input[i].serv_addr), (struct sockaddr*) &addrs[i], sizeof(struct sockaddr));
        sockfd[i] = socket(AF_INET, SOCK_STREAM, 0);
        thread_input[i].sockfd = sockfd[i];
        thread_input[i].id = i;

        printf("In main: creating thread %i\n", i);
        rc = pthread_create(&t_id[i], NULL, send_data, (input_t *)&thread_input[i]);
        if (rc)
        {
            printf("Maint Thread | ERROR creating thread %i: return code %d\n", i, rc);
            exit(-1);
       }
    }

    if (listen(sockfd[THREADS_NUM], 1) == 0)
    {
         printf("Main Thread | Connection arrived \n");
    }

    if ( (connfd = accept(sockfd[THREADS_NUM], (struct sockaddr*)NULL, NULL)) < 0 )
    {
        printf("Main Thread | accept(): error %s\n", strerror(errno));
        intHandler();
    }

    struct sockaddr_in* addr = (struct sockaddr_in*) &(addrs[THREADS_NUM]);
    printf("Main Thread | Connected to %s\n", inet_ntoa(addr->sin_addr));
 

    while(1)
    {
        // Lock all mutex
        for (i = 0; i < THREADS_NUM; i++)
        {
            pthread_mutex_lock(&mutex[i]);
        }
        memset(recv_buff, '0', sizeof(recv_buff));

        if ((bytes = recv(connfd, recv_buff, sizeof(recv_buff)-1, 0)) < 0)
        {
            printf("Main Thread | recv(): %s\n", strerror(errno));
            intHandler();
        }
        else
        {
            printf("Main Thread | Received %i bytes\n", bytes);
        }
                
        for (i = 0; i < THREADS_NUM; i++)
        {
            pthread_cond_broadcast(&tx_cond[i]); //Notify to all threads to TX
            pthread_mutex_unlock(&mutex[i]);
        }
    }

}