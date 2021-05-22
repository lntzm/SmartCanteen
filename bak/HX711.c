#include <stdio.h>
#include <wiringPi.h>
#include <fcntl.h>

/*-----------------结构体-----------------*/
struct hx711_pin
{
    int SCK;
    int SDA;
    int EN;              //校准使能
    int calibration;     //校准
    int coefficient;     //比例系数
    int weight;          //重量
    unsigned long value; //记录数值
};

void set_pin(struct hx711_pin *value)
{
    value->SCK = 2;
    value->SDA = 3;
    value->EN = 1;
    value->coefficient = 415;
}

void init_pin(struct hx711_pin *value)
{
    pinMode(value->SCK, OUTPUT);
    pinMode(value->SDA, INPUT);
    pullUpDnControl(value->SDA, PUD_UP);
}

void start(struct hx711_pin *value)
{
    int i;
    digitalWrite(value->SCK, LOW); //使能AD
    while (digitalRead(value->SCK))
        value->value = 0;           //数值
    while (digitalRead(value->SDA)) //AD转换未结束则等待。
        delay(100);
    for (i = 0; i < 24; i++)
    {
        digitalWrite(value->SCK, HIGH);
        while (0 == digitalRead(value->SCK))
            delay(1000);
        value->value = value->value * 2;
        digitalWrite(value->SCK, LOW);
        while (digitalRead(value->SCK))
            if (digitalRead(value->SDA))
                value->value = value->value + 1;
    }
    digitalWrite(value->SCK, HIGH);
    digitalWrite(value->SCK, LOW);
    if ((value->EN == 1) && (value->value < 25000))
    {
        value->EN = 0;
        value->calibration = value->value;
    }
    else
    {
        i = (value->value - value->calibration + 50) / value->coefficient;
    }
    if (i < 5000)
        value->weight = i;
    printf("重量为：%d g\n", value->weight);
}

/*-----------------主体-----------------*/
int setup(struct hx711_pin *value)
{
    if (wiringPiSetup() == -1)
        return 1;
    set_pin(value);
    init_pin(value);
    return 0;
}

void loop(struct hx711_pin *value)
{
    while (1)
        start(value);
}

int main(void)
{
    struct hx711_pin value;
    if (0 == setup(&value))
        loop(&value);
    return 0;
}
