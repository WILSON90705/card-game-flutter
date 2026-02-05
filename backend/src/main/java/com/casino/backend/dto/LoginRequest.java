package com.casino.backend.dto;

public class LoginRequest {
    private String usuario;
    private String password;

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

/*
 * class LoginResponse {
 * 
 * private boolean success;
 * private String message;
 * 
 * public LoginResponse(boolean success, String message) {
 * this.success = success;
 * this.message = message;
 * }
 * 
 * public boolean isSuccess() {
 * return success;
 * }
 * 
 * public String getMessage() {
 * return message;
 * }
 * }
 */