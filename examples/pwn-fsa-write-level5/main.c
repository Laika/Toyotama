#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void init(){
    setbuf(stdin, NULL);
    setbuf(stdout, NULL);
    setbuf(stderr, NULL);
}

void show_flag(){
    printf("\nExcellent!\n");
    system("cat FLAG");
}

void show_stack(void *ptr){
    printf("\n######## STACK ARENA #######\n\n");
    printf("%-8s|%13s\n", "[Ofset]", "[Value]");
    printf("========+===================\n");
    for(int i = 0; i < 8; i++){
        unsigned long *p = &((unsigned long*)ptr)[i];
        printf(" 0x%04x | 0x%016lx ", i*8, *p);
        if(i == 0) printf(" <- Can you rewrite this value?");
        if(i == 1) printf(" <- Target address");
        if(i > 1) printf(" |");
        printf("\n--------+------------------- ");
        if(i != 0){
            if(i == 1 || i == 7) printf(" -");
            else printf(" |");
            if(i == 4) printf(" Buffer");
        }
        printf("\n");
    }
    for(int i = 0; i < 3; i++) printf("%4s%5s%10s\n", ".", "|", ".");
    printf("========+===================\n\n");
}

int main(){
    char buf[0x30];
    long long int *p = NULL;
    long long int cafe = 0xcafe;
    p = &cafe;

    init();
    show_stack(&cafe);
    printf("Input your message.\n> ");
    fgets(buf, sizeof(buf), stdin);
    printf(buf);
    show_stack(&cafe);
    printf("...Recorded.\n");
    
    if(cafe != 0xcafe) show_flag();

    return 0;
}