package com.casino.backend.model;

import jakarta.persistence.*;

@Entity
@Table(name = "logueado")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(nullable = false)
    private String usuario;

    @Column(nullable = false)
    private String password;

    public User() {
    };

    public User(String usuario, String password) {
        this.usuario = usuario;
        this.password = password;
    }

    public Long getId() {
        return id;
    }

    public String getUsuario() {
        return usuario;
    }

    public String getPassword() {
        return password;
    }

    public void setUsuario(String usuario) {
        this.usuario = usuario;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}
