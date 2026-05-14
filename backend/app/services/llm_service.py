import ollama

estrategias_retencion = {
    "Near_Location": "Instrucción: El cliente no vive ni trabaja cerca del gimnasio, lo que dificulta su asistencia. Ofrécele acceso gratuito a las clases virtuales premium para que entrene desde casa cuando no pueda viajar.",
    
    "Partner": "Instrucción: El cliente pertenece a una empresa asociada (convenio corporativo). Recuérdale su estatus VIP y ofrécele un pase de invitado de 3 días GRATIS para que traiga a un compañero de trabajo.",
    
    "Promo_friends": "Instrucción: El cliente se inscribió por recomendación de un amigo. Ofrécele un pase doble exclusivo de fin de semana para que invite a su amigo a entrenar juntos y recupere la motivación.",
    
    "Contract_period": "Instrucción: El cliente tiene un contrato de corto plazo y es propenso a no renovar. Ofrécele hacer un 'upgrade' a un plan semestral o anual dándole el primer mes al 50% de descuento.",
    
    "Group_visits": "Instrucción: El cliente no está participando en clases grupales (falta de comunidad). Invítalo a una clase de prueba de alta energía (ej. Spinning o Funcional) totalmente GRATIS y prométele un ambiente divertido.",
    
    "Age": "Instrucción: El perfil de edad del cliente indica que necesita un enfoque más personalizado. Ofrécele una evaluación física de 30 minutos con un entrenador experto, totalmente GRATIS, para rediseñar su rutina.",
    
    "Avg_additional_charges_total": "Instrucción: El cliente no consume los servicios adicionales (cafetería, tienda, masajes). Regálale un cupón o un batido de proteínas GRATIS para canjear en su próxima visita y motivarlo a ir.",
    
    "Month_to_end_contract": "Instrucción: El contrato está por vencer. Ofrécele un 15% de descuento SÓLO si renueva hoy.",
    
    "Lifetime": "Instrucción: El cliente es relativamente nuevo y no ha logrado formar el hábito. Ofrécele una sesión de 're-inducción' personalizada para ayudarle a fijar metas realistas, sin ningún costo.",
    
    "Avg_class_frequency_current_month": "Instrucción: El cliente ha tenido un nivel de asistencia muy bajo en todo el mes. Plantéale un reto rápido: si asiste 3 veces esta misma semana, se gana una toalla o termo del gimnasio GRATIS.",
    
    "caida_frecuencia": "Instrucción: El cliente ha dejado de venir. Anímalo a volver ofreciéndole un entrenamiento grupal GRATIS o una rutina nueva gratis con un entrenador GRATIS."
}

def generar_sugerencia(motivo):
    
    instruccion_estrategica = estrategias_retencion.get(motivo, "Ofrécele un descuento general del 10%.")


    prompt= f"""Eres un asistente para retención de clientes en un gimnasio. Redacta UN SOLO mensaje de Telegram.
    REGLAS ESTRICTAS:
    1. MÁXIMO 3 LÍNEAS.
    2. Tono amigable y persuasivo.
    3. NUNCA menciones riesgos, abandono, ni probabilidades.

    Contexto del cliente:
    - Problema: {instruccion_estrategica}

    Mensaje de Telegram:"""

    modelo = ['phi3']

    print(f"Modelo: {modelo.upper()}")
    try:
        respuesta = ollama.chat(model=modelo, messages=[{'role': 'user', 'content': prompt}], options={'temperature': 0.1}) 
        mensaje = respuesta['message']['content']
        print(f"{mensaje}\n{'-'*40}")
    except Exception as e:
        print(f"Error: {e}")
    