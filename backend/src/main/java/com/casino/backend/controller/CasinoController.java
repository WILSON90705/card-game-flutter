package com.casino.backend.controller;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.ResponseEntity;
import com.casino.backend.service.UserService;
import com.casino.backend.dto.LoginRequest;
import com.casino.backend.dto.RegisterRequest;

@CrossOrigin(origins = "http://localhost:8080")
@RestController
@RequestMapping("/casino")
public class CasinoController {
    private final UserService userService;

    public CasinoController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest loginRequest) {
        try {
            userService.login(loginRequest.getUsuario(), loginRequest.getPassword());
            return ResponseEntity.status(200).body("Login successful");
        } catch (RuntimeException e) {
            return ResponseEntity.status(400).body(e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(500).body("An error occurred: " + e.getMessage());
        }

    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterRequest registerRequest) {
        try {
            userService.register(registerRequest.getUsuario(), registerRequest.getPassword());
            return ResponseEntity.status(200).body("Registration successful");
        } catch (RuntimeException e) {
            return ResponseEntity.status(400).body(e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(500).body("An error occurred: " + e.getMessage());
        }
    }

}
