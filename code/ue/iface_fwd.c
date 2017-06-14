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
#define TRIGGER_PORT    2004

#define THREADS_NUM     1
#define SOCKS_NUM       3
#define BUFFER_SIZE     4096
#define MAX_PKTS        2048

pthread_t               t_id [THREADS_NUM]; //ids for threads
pthread_cond_t          tx_cond [THREADS_NUM];
pthread_mutex_t         mutex [THREADS_NUM];

char                    recv_buff[MAX_PKTS][BUFFER_SIZE]; //shared variable. Read-only.
unsigned int            sockfd[SOCKS_NUM]; // Close all sockets when prgm is interrupted
unsigned int            bytes[MAX_PKTS]; //shared variable. Read-only
unsigned int            data_available[THREADS_NUM]; //conditional variable
unsigned int            last_write; //main thread writes
int                     pkts_read[THREADS_NUM][MAX_PKTS];
int                     kill_thread;

typedef struct input_thread
{
    int sockfd;
    struct sockaddr serv_addr;
    int id;
} 
input_t;

void intHandler() 
{
    unsigned int i = 0;

    for (i = 0; i < THREADS_NUM; i++)
    {  
        pthread_mutex_destroy(&mutex[i]);
        pthread_cond_destroy(&tx_cond[i]);
        pthread_cancel(t_id[i]);
    }

    for (i=0; i < SOCKS_NUM; i++)
    {
        close(sockfd[i]);
    }
    //printf("\nClear! \n");
    exit(0);
}

// Routine for consumer threads
void * send_data(void *input_args)
{
    input_t * args = (input_t*)input_args;
    char buff [MAX_PKTS][BUFFER_SIZE];
    int buff_bytes[MAX_PKTS];

    int last_read = 0;
    int last_read_cpy = 0;
    int last_write_cpy = 0;
    int i = 0;
    int counter = 0;
    int limit_loop = 0;
    args->sockfd = socket(AF_INET, SOCK_STREAM, 0);

    if( (connect(args->sockfd, (struct sockaddr *)&(args->serv_addr), 
        sizeof(args->serv_addr))) < 0)
    {
       printf("Thread %i  | connect(): %s\n", args->id, strerror(errno));
       pthread_exit(0);
    }

    struct sockaddr_in* addr = (struct sockaddr_in*) &(args->serv_addr);
    printf("Thread %i  | Connected to %s\n", 
        args->id , inet_ntoa(addr->sin_addr)); 

    while(1)
    {
        // Critical section
        //printf("Thread %i | Trying to lock mutex\n", args->id);
        pthread_mutex_lock(&mutex [args->id]);
        //printf("Thread %i | Lock mutex\n", args->id);
        while (data_available[args->id] == 0)
        {
        //    printf("Thread %i | Waiting\n", args->id);
            pthread_cond_wait(&tx_cond [args->id], &mutex [args->id]);
        }

        if (kill_thread)
        {
            printf("Thread %i | Closing socket and exiting...\n", args->id);
            close(args->sockfd);
            kill_thread = 0;
            pthread_mutex_unlock(&mutex [args->id]);
            pthread_exit(0);
        }

        last_write_cpy = last_write;
        last_read_cpy = last_read;
        limit_loop = last_write_cpy;
        counter = 0;
        
        if ( last_read > last_write_cpy ) //Start again
        {
            limit_loop = MAX_PKTS;
            for (i = last_read; i <= limit_loop; i++)
            {
                if( i == MAX_PKTS )
                {
                    i = 0;
                    limit_loop = last_write_cpy;
                }
                
                memcpy((char*)buff[counter], recv_buff[i], BUFFER_SIZE*sizeof(char));
                buff_bytes[counter] = bytes[i];
                pkts_read[args->id][i] = 1;
                last_read = i;
                counter++;
                if ( i == last_write_cpy)
                {
                    i = MAX_PKTS+1;
                }
            }
        }
        else
        {
            for (i = last_read; i <= last_write_cpy; i++)
            {
                if( i == MAX_PKTS )
                {
                    i = 0;
                }
                memcpy((char*)buff[counter], (char*)recv_buff[i], bytes[i]);
                buff_bytes[counter] = bytes[i];
                pkts_read[args->id][i] = 1;
                last_read = i;
                counter++;
            }
        }
        
        data_available[args->id] = 0;
        // End of critical section
        pthread_mutex_unlock(&mutex [args->id]);
       // printf("Thread %i | Unlock mutex\n", args->id);
        //printf("Thread %i | last_write %i, last_read %i counter %i diff %i\n", args->id, last_write_cpy, last_read_cpy, counter, (last_write_cpy - last_read_cpy));
        for (i = 0; i < counter; i++)
        {
            if (buff_bytes[i] <= 0)
            {
                printf("Thread %i | Exiting...\n", args->id);
                pthread_exit(0);
            }
        //    printf("Thread %i | Sending packet: %i bytes\n", args->id, buff_bytes[i]);
            sendto(args->sockfd, buff[i], buff_bytes[i], 0, NULL, 0);
        //    printf("Thread %i | iteration: %i \n", args->id, i);
        }     
    }
} 

int main (int argc, char *argv[])
{
    if (argc != 2 )
    {
        //printf("%s <D2D IP Address>\n", argv[0]);
        exit(0);
    }

    int connfd = 0;
    struct sockaddr_in addrs[SOCKS_NUM];
    char* d2d_addr = argv[1];

    sockfd[SOCKS_NUM-1] = socket(AF_INET, SOCK_STREAM, 0);
    memset(&addrs[THREADS_NUM], '0', sizeof(struct sockaddr));
    memset(recv_buff, '0', sizeof(recv_buff));

    addrs[SOCKS_NUM-1].sin_family = AF_INET;
    addrs[SOCKS_NUM-1].sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addrs[SOCKS_NUM-1].sin_port = htons(LOCAL_PORT); 

    bind(sockfd[SOCKS_NUM-1], (struct sockaddr*)&addrs[SOCKS_NUM-1], 
            sizeof(struct sockaddr_in));
    
    // Catching ctrl-C and sigpipe signals
    signal(SIGINT, intHandler);
    signal(SIGPIPE, intHandler);

    // D2D address
    memset(&addrs[0], '0', sizeof(struct sockaddr));
    addrs[0].sin_family = AF_INET;
    addrs[0].sin_addr.s_addr = inet_addr(d2d_addr);
    addrs[0].sin_port = htons(FWD_D2D_PORT);

    // Loopback address
    memset(&addrs[1], '0', sizeof(struct sockaddr));
    addrs[1].sin_family = AF_INET;
    addrs[1].sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addrs[1].sin_port = htons(FWD_LTE_PORT);

    input_t thread_input[THREADS_NUM]; //input for threads

    unsigned int i = 0;
    int rc = 1;
    
    //Creates the mutexes and threads
    for (i = 0; i < THREADS_NUM; i++) 
    {
        pthread_mutex_init (&mutex[i], NULL);
        pthread_cond_init(&tx_cond[i], NULL);
        data_available[i] = 0;
        last_write = 0;

        memcpy((struct sockaddr*)&(thread_input[i].serv_addr), (struct sockaddr*) &addrs[i], 
                    sizeof(struct sockaddr));
        thread_input[i].sockfd = 0;
        thread_input[i].id = i;
        memset((void*) pkts_read[i], 0, MAX_PKTS*sizeof(int));

    }

    sockfd[1] = socket(AF_INET, SOCK_STREAM, 0);
    if( (connect(sockfd[1], (struct sockaddr *) &addrs[1], sizeof(struct sockaddr))) < 0)
    {
        printf("Main Thread | connect(): %s\n", strerror(errno));
        intHandler();
    }

    if (listen(sockfd[SOCKS_NUM-1], 1) == 0)
    {
         printf("Main Thread | Connection arrived \n");
    }

    if ( (connfd = accept(sockfd[SOCKS_NUM-1], (struct sockaddr*)NULL, NULL)) < 0 )
    {
        printf("Main Thread | accept(): %s\n", strerror(errno));
        intHandler();
    }

    struct sockaddr_in* addr = (struct sockaddr_in*) &(addrs[SOCKS_NUM-1]);
    printf("Main Thread | Connected to %s\n", inet_ntoa(addr->sin_addr));
    int writing_counter = -1;

    while(1)
    {
        // Lock all mutex

        //printf("Main Thread | Trying to lock mutex %i\n", i);
        pthread_mutex_lock(&mutex[0]);
        //printf("Main Thread | Lock mutex %i\n", i);
  
        if (writing_counter == (MAX_PKTS - 1) )
        {
            writing_counter = -1;
        }

        writing_counter++;
        last_write = writing_counter;
        
        //memset((void*) recv_buff[writing_counter], 0, sizeof(char)*BUFFER_SIZE);

        if ((bytes[writing_counter] = recv(connfd, recv_buff[writing_counter], sizeof(char)*BUFFER_SIZE, 0)) < 0)
        {
            printf("Main Thread | recv(): %s\n", strerror(errno));
            intHandler();
        }
     /* else
        {
            //printf("Main Thread | Received %i bytes\n", bytes);
        }
      */ 

        if (strstr(recv_buff[writing_counter], "TRIGGER") != NULL )
        {
            printf("Main Thread | Trigger found! writing_counter %i \n", writing_counter);
            if (rc)
            {
                printf("Main main | creating thread\n");
                rc = pthread_create(&t_id[0], NULL, send_data, (input_t *)&thread_input[0]);
                if (rc)
                {
                    printf("Main Thread | pthread_create(): %s\n", strerror(errno));
                    exit(-1);
                }
                kill_thread = 0;
            }
        }
        if (strstr(recv_buff[writing_counter], "DISABLE") != NULL )
        {
            printf("Main Thread | Disable trigger found! \n");
            printf("Main Thread | canceling thread\n");
            kill_thread = 1;
            rc = 1;
        }

        //printf("Main Thread | Sending %i bytes\n", bytes[writing_counter]);
        sendto(sockfd[1], recv_buff[writing_counter], bytes[writing_counter], 0, NULL, 0);
        //printf("Main Thread | last_write %i \n", writing_counter);        

        data_available[0] = 1;
            //printf("Main Thread | Notifying thread %i\n", i);

        pthread_mutex_unlock(&mutex[0]);
        pthread_cond_broadcast(&tx_cond[0]); //Notify to all threads to TX
        //printf("Main Thread | Unlock mutex %i\n", i);
    }

}