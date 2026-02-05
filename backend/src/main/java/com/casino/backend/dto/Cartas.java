package com.casino.backend.dto;

public class Cartas {
    private int id;
    private String simbolo;
    private String numero;

    public String getsimbolo() {
        return simbolo;

    }

    public String getnumero() {
        return numero;
    }

    public int getId() {
        return id;
    }

    public void setsimbolo(String simbolo) {
        this.simbolo = simbolo;
    }

    public void setnumero(String numero) {
        this.numero = numero;
    }

    public void setId(int id) {
        this.id = id;
    }
}