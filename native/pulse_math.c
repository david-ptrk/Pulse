// pulse_math.c
#include <stdio.h>
#include <math.h>
#include <string.h>

static char _err_buf[256] = {0};

const char *pulse_math_last_error(void)
{
    return _err_buf[0] ? _err_buf : NULL;
}

static void set_err(const char *msg)
{
    strncpy(_err_buf, msg, sizeof(_err_buf) - 1);
    _err_buf[sizeof(_err_buf) - 1] = '\0';
}

static void clear_err(void)
{
    _err_buf[0] = '\0';
}

double pulse_sqrt(double x)
{
    clear_err();
    if (x < 0)
    {
        set_err("sqrt() argument must be non-negative");
        return NAN;
    }
    return sqrt(x);
}

double pulse_floor(double x)
{
    clear_err();
    return floor(x);
}

double pulse_ceil(double x)
{
    clear_err();
    return ceil(x);
}

double pulse_log(double x, int use_base, double base)
{
    clear_err();
    if (x <= 0)
    {
        set_err("log() argument must be positive");
        return NAN;
    }
    if (!use_base)
        return log(x);
    if (base <= 0 || base == 1)
    {
        set_err("log() base must be positive and not 1");
        return NAN;
    }
    return log(x) / log(base);
}

double pulse_log2(double x)
{
    clear_err();
    if (x <= 0)
    {
        set_err("log2() argument must be positive");
        return NAN;
    }
    return log2(x);
}

double pulse_log10(double x)
{
    clear_err();
    if (x <= 0)
    {
        set_err("log10() argument must be positive");
        return NAN;
    }
    return log10(x);
}

double pulse_exp(double x)
{
    clear_err();
    return exp(x);
}

double pulse_sin(double x)
{
    clear_err();
    return sin(x);
}

double pulse_cos(double x)
{
    clear_err();
    return cos(x);
}

double pulse_tan(double x)
{
    clear_err();
    return tan(x);
}

double pulse_abs(double x)
{
    clear_err();
    return fabs(x);
}

double pulse_pow(double base, double exp)
{
    clear_err();
    return pow(base, exp);
}