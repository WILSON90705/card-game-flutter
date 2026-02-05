//logica de la api
package com.casino.backend.service;

//import java.lang.StackWalker.Option;
import org.springframework.stereotype.Service;
import org.springframework.security.crypto.password.PasswordEncoder;
import com.casino.backend.repository.UserRepository;
import com.casino.backend.model.User;
// import java.util.Optional;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public UserService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;

    }

    public boolean login(String usuario, String password) {

        User user = userRepository.findByUsuario(usuario)
                .orElseThrow(() -> new RuntimeException("Usuario no encontrado"));

        if (!passwordEncoder.matches(password, user.getPassword())) {
            throw new RuntimeException("Contraseña incorrecta");
        }

        return passwordEncoder.matches(password, user.getPassword());
    }

    public boolean register(String usuario, String password) {
        String encodedPassword = passwordEncoder.encode(password);
        User user = new User();

        if (userRepository.findByUsuario(usuario).isPresent() && !encodedPassword.matches(encodedPassword)) {
            throw new RuntimeException("El usuario ya existe");
        }
        user.setUsuario(usuario);
        user.setPassword(encodedPassword);
        userRepository.save(user);
        return passwordEncoder.matches(password, user.getPassword());
    }
    /*
     * public boolean carta(String valor, String )
     */

    public boolean retornoJugador(String usuario) {

        return true;
    }
}
